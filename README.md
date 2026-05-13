# Eclipse ThreadX Documentation

This repository contains the AsciiDoc source for the [Eclipse ThreadX](https://threadx.io/) documentation. The project team generates the HTML website from the contents of this repository.

If you want to propose changes or additions to the documentation, this is the right place!

## Generating the Website

The documentation website is generated using [Antora](https://antora.org/). To build it locally:

1. Install Antora:
   ```
   npm install -g @antora/cli @antora/site-generator
   ```
2. From the repository root, run:
   ```
   antora antora-playbook.yml
   ```
3. The generated site will be output to the `../rtos-docs-html` directory.

## What is Eclipse ThreadX?

Eclipse ThreadX is a real-time operating system (RTOS) for Internet of Things (IoT) and edge devices powered by microcontroller units (MCUs). Eclipse ThreadX is designed to support most highly constrained devices (battery powered and having less than 64 KB of flash memory).

**IMPORTANT:** Microsoft Azure RTOS, an embedded development suite with the ThreadX real-time operating system, has been deployed on more than 12 billion devices worldwide. Azure RTOS has now transitioned to an open-source project under the stewardship of the Eclipse Foundation, a recognized leader in hosting open-source IoT projects.

With Eclipse Foundation as the new home, Azure RTOS becomes Eclipse ThreadX. For more information, see:

- [Microsoft IoT blog](https://techcommunity.microsoft.com/t5/internet-of-things-blog/microsoft-contributes-azure-rtos-to-open-source/ba-p/3986318)
- [Eclipse ThreadX project](https://threadx.io/)

## Eclipse ThreadX Resources

- [Eclipse ThreadX repositories](https://github.com/eclipse-threadx/)
- [Eclipse ThreadX documentation](https://threadx.io/)

## Components of Eclipse ThreadX

The Eclipse ThreadX platform is the collection of run-time solutions including ThreadX, NetX Duo, FileX, GUIX and USBX.

### ThreadX

ThreadX is an advanced Real-Time Operating System (RTOS) designed specifically for deeply embedded applications. Among the multiple benefits ThreadX provides are advanced scheduling facilities, message passing, interrupt management, and messaging services. ThreadX has many advanced features, including its picokernel architecture, preemption-threshold scheduling, event-chaining, and a rich set of system services.

### FileX

FileX is a high-performance FAT-compatible file system. It is fully integrated with ThreadX and is available for all supported processors. Like ThreadX, FileX is designed to have a small footprint and high performance, making it ideal for today's deeply embedded applications that require file operations. FileX supports most physical media, including RAM disk, USBX, SD CARD, and NAND/NOR flash memories via LevelX.

### GUIX

GUIX is a professional quality graphical user interface package, created to meet the needs of embedded systems developers. Unlike the alternatives, GUIX is small, fast, and easily ported to virtually any hardware configuration capable of supporting graphical output. GUIX also delivers exceptional visual appeal and an intuitive and powerful API for application-level user interface development.

### NetX Duo

NetX Duo is an advanced, Industrial Grade TCP/IP network stack designed specifically for deeply embedded, real-time, and IoT applications. NetX Duo is a dual IPv4 and IPv6 network stack.

### USBX

USBX is a high-performance USB host, device, and On-The-Go (OTG) embedded stack. It is fully integrated with ThreadX and is available for all ThreadX supported processors. Like ThreadX, USBX is designed to have a small footprint and high performance, making it ideal for deeply embedded applications that require an interface with USB devices.

### Windows Tools

GUIX Studio provides a complete GUI application design environment, facilitating the creation and maintenance of all graphical elements in the application's GUI. GUIX Studio automatically generates C code compatible with the GUIX library, ready to be compiled and run on the target.

TraceX is a host-based analysis tool that provides developers with a graphical view of real-time system events and enables them to visualize and better understand the behavior of their real-time systems.

## The Eclipse ThreadX Advantage

Eclipse ThreadX provides the following advantages over other real-time operating systems.

### Most Deployed RTOS

Eclipse ThreadX has over 12 billion deployments worldwide. The popularity of Eclipse ThreadX is a testament to its reliability, quality, size, performance, advanced features, ease-of-use, and overall time-to-market advantages.

### Intuitive and Consistent API Design

- Intuitive and consistent API.
- Noun-verb naming convention.
- All APIs have leading prefix, such as _tx__ for ThreadX and _fx__ for FileX, to easily identify the Eclipse ThreadX component they belong to.
- Functional consistency throughout the APIs. For example, all API functions that suspend have an optional timeout that functions in an identical manner.
- Many APIs are directly available from application ISRs.
- Optional user-notification callbacks for media and file operations.
- Event-driven programming model (API).

### High Efficiency

- Small code footprint.
- Scalable code footprint based on the services used.
- Fast execution. Eclipse ThreadX is designed for speed and has minimal internal function call layering to help achieve the fastest possible performance.

### Fastest Time-to-Market

Eclipse ThreadX is easy to install, learn, use, debug, verify, certify, and maintain. As a result, Eclipse ThreadX is one of the most popular real-time operating systems for embedded IoT devices. Our consistent time-to-market advantage is built on:

- Complete source code availability.
- Easy-to-use API.
- Comprehensive and advanced feature set.
- Quality documentation.

### Full, Highest-Quality Source Code

Throughout the years, Eclipse ThreadX source code has set the bar in quality and ease of understanding. In addition, the convention of having one function per file provides for easy source navigation.

### Pre-Certified by SGS-TÜV Saar

Eclipse ThreadX has been certified by SGS-TÜV Saar for use in safety-critical systems, according to IEC-61508 SIL 4. The certification confirms that Eclipse ThreadX can be used in the development of safety-related software for the highest safety integrity levels of IEC-61508 for the "Functional Safety of electrical, electronic, and programmable electronic safety-related systems." SGS-TUV Saar, formed through a joint venture of Germany's SGS-Group and TUV Saarland, has become the leading accredited, independent company for testing, auditing, verifying, and certifying embedded software for safety-related systems worldwide.

Artifacts (Certificate, Safety Manual, Test Report, etc.) associated with the TÜV certification are available to license. Please visit [the ThreadX Alliance website](https://threadxalliance.org) for more details.
